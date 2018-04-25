pragma solidity ^0.4.0;

/**
 * @title SafeMath
 * @dev Math operations with safety checks that throw on error
 */
library SafeMath {

    /**
    * @dev Multiplies two numbers, throws on overflow.
    */
    function mul(uint256 a, uint256 b) internal pure returns (uint256 c) {
        if (a == 0) {
            return 0;
        }
        c = a * b;
        assert(c / a == b);
        return c;
    }

    /**
    * @dev Integer division of two numbers, truncating the quotient.
    */
    function div(uint256 a, uint256 b) internal pure returns (uint256) {
        // assert(b > 0); // Solidity automatically throws when dividing by 0
        // uint256 c = a / b;
        // assert(a == b * c + a % b); // There is no case in which this doesn't hold
        return a / b;
    }

    /**
    * @dev Subtracts two numbers, throws on overflow (i.e. if subtrahend is greater than minuend).
    */
    function sub(uint256 a, uint256 b) internal pure returns (uint256) {
        assert(b <= a);
        return a - b;
    }

    /**
    * @dev Adds two numbers, throws on overflow.
    */
    function add(uint256 a, uint256 b) internal pure returns (uint256 c) {
        c = a + b;
        assert(c >= a);
        return c;
    }
}

/*
    A Trading Contract for order processing in CPChain.
    Note: This is experimental, don't use it in main-net for now.
*/
contract Trading {

    using SafeMath for uint256;

    enum State {
        Created,
        Delivered,
        Confirmed,
        Finished,
        Rated,
        Disputed,
        Withdrawn
    }

    struct OrderInfo {
        bytes32 descHash;
        bytes buyerRSAPubkey;
        address buyerAddress;
        address sellerAddress;
        address proxyAddress;
        address secondaryProxyAddress;
        uint offeredPrice;
        uint proxyFee;
        bytes32 deliverHash;
        uint endTime;
        State state;
    }

    uint public numOrders = 0;
    // TODO let records to be public or only let relevant address to be a accessible
    mapping(uint => OrderInfo) public orderRecords;

    mapping(address => uint) public proxyCredits;

    // Security Checks
    modifier onlyBefore(uint time) { require(now < time); _; }
    modifier onlyAfter(uint time) { require(now > time); _; }
    modifier onlyBuyer(uint id) { require(msg.sender == orderRecords[id].buyerAddress); _; }
    modifier onlySeller(uint id) { require(msg.sender == orderRecords[id].sellerAddress); _; }
    modifier onlyProxy(uint id) {
        require(
            msg.sender == orderRecords[id].proxyAddress ||
            msg.sender == orderRecords[id].secondaryProxyAddress
        );
        _;
    }
    modifier inState(uint id, State _state) { require(orderRecords[id].state == _state); _; }

    function Trading() public {
    }

    function() payable {
    }

    // Some events that help tracking the status of the chain
    event OrderInitiated(
        address from,
        uint orderId,
        uint value
    );
    event OrderWithdrawn(address from);
    event OrderConfirmed(address from);
    event OrderDisputed(address from);
    event SellerClaimTimeout(address from);
    event ProxyClaimRelay(address from);
    event ProxyHandleDispute(address from);
    event ProxyRated(address from);
    event OrderFinalized(uint id);


    function placeOrder(
        bytes32 descHash,
        bytes buyerRSAPubkey,
        address seller,
        address proxy,
        address secondaryProxy,
        uint proxyFee,
        uint timeAllowed
    )
        public
        payable
    {
        require(msg.value > proxyFee.mul(2));
        uint thisID = numOrders.add(1);
        orderRecords[thisID] = OrderInfo({
            descHash: descHash,
            buyerRSAPubkey: buyerRSAPubkey,
            buyerAddress: msg.sender,
            sellerAddress: seller,
            proxyAddress: proxy,
            secondaryProxyAddress: secondaryProxy,
            deliverHash: bytes32(0),
            offeredPrice: msg.value,
            proxyFee: proxyFee,
            endTime: now.add(timeAllowed),
            state: State.Created
        });
        OrderInitiated(msg.sender, thisID, msg.value);
    }

    function buyerWithdraw(uint id)
        public
        onlyBuyer(id)
        onlyBefore(orderRecords[id].endTime)
        inState(id, State.Created)
    {
        orderRecords[id].state = State.Withdrawn;
        orderRecords[id].buyerAddress.transfer(orderRecords[id].offeredPrice);
        OrderWithdrawn(msg.sender);
    }

    function buyerDispute(uint id)
        public
        onlyBuyer(id)
        onlyBefore(orderRecords[id].endTime)
        inState(id, State.Delivered)
    {
        orderRecords[id].state = State.Disputed;
        OrderDisputed(msg.sender);
    }

    function proxyJudge(uint id, bool decision)
        public
        onlyProxy(id)
        onlyBefore(orderRecords[id].endTime)
        inState(id, State.Disputed)
    {
        if (decision == true)
            finalizeOrder(id, orderRecords[id].sellerAddress);
        else
            finalizeOrder(id, orderRecords[id].buyerAddress);

        ProxyHandleDispute(msg.sender);
    }

    function deliverMsg(bytes32 deliverHash, uint id)
        public
        onlyProxy(id)
        onlyBefore(orderRecords[id].endTime)
        inState(id, State.Created)
    {
        orderRecords[id].deliverHash = deliverHash;
        orderRecords[id].state = State.Delivered;
        ProxyClaimRelay(msg.sender);
    }

    function confirmDeliver(uint id)
        public
        onlyBuyer(id)
        onlyBefore(orderRecords[id].endTime)
        inState(id, State.Delivered)
    {
        orderRecords[id].state = State.Confirmed;
        finalizeOrder(id, orderRecords[id].sellerAddress);
        OrderConfirmed(msg.sender);
    }

    function sellerClaimTimedOut(uint id)
        public
        onlySeller(id)
        inState(id, State.Delivered)
        onlyAfter(orderRecords[id].endTime)
    {
        finalizeOrder(id, orderRecords[id].sellerAddress);
        SellerClaimTimeout(msg.sender);
    }

    function sellerRateProxy(uint id, uint rate)
        public
        onlySeller(id)
        inState(id, State.Finished)
    {
        require(rate >= 0 && rate <= 100);
        orderRecords[id].state = State.Rated;
        proxyCredits[orderRecords[id].proxyAddress] =
            proxyCredits[orderRecords[id].proxyAddress].add(rate);
        proxyCredits[orderRecords[id].secondaryProxyAddress] =
            proxyCredits[orderRecords[id].secondaryProxyAddress].add(rate);
        ProxyRated(msg.sender);
    }

    function buyerRateProxy(uint id, uint rate)
        public
        onlyBuyer(id)
        inState(id, State.Finished)
    {
        require(rate >= 0 && rate <= 100);
        orderRecords[id].state = State.Rated;
        proxyCredits[orderRecords[id].proxyAddress] =
            proxyCredits[orderRecords[id].proxyAddress].add(rate);
        proxyCredits[orderRecords[id].secondaryProxyAddress] =
            proxyCredits[orderRecords[id].secondaryProxyAddress].add(rate);
        ProxyRated(msg.sender);
    }

    function finalizeOrder(uint id, address beneficiary)
        private
    {
        orderRecords[id].state = State.Finished;
        uint payProxy = orderRecords[id].proxyFee;
        uint payBeneficiary = orderRecords[id].offeredPrice.sub(payProxy.mul(2));
        beneficiary.transfer(payBeneficiary);
	    // FIXME
	// this logic is wrong.
        orderRecords[id].proxyAddress.transfer(payProxy);
        orderRecords[id].secondaryProxyAddress.transfer(payProxy);
        OrderFinalized(id);
    }

}
