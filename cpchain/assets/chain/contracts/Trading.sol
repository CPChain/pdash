pragma solidity ^0.4.0;

/*
    A Trading Contract for order processing in CPChain.
*/
contract Trading {

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

    uint public timeAllowed = 600; // Unit is second
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

    event OrderInitiated(
        address indexed from,
        uint orderId,
        uint value
    );

    function placeOrder(
        bytes32 descHash,
        address seller,
        address proxy,
        address secondaryProxy,
        uint proxyFee
    )
        public
        payable
    {
        uint thisID = numOrders++;
        orderRecords[thisID] = OrderInfo({
            descHash: descHash,
            buyerAddress: msg.sender,
            sellerAddress: seller,
            proxyAddress: proxy,
            secondaryProxyAddress: secondaryProxy,
            deliverHash: bytes32(0),
            offeredPrice: msg.value,
            proxyFee: proxyFee,
            endTime: now + timeAllowed,
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
    }

    function buyerDispute(uint id)
        public
        onlyBuyer(id)
        onlyBefore(orderRecords[id].endTime)
        inState(id, State.Delivered)
    {
        orderRecords[id].state = State.Disputed;
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
    }

    function deliverMsg(bytes32 deliverHash, uint id)
        public
        onlyProxy(id)
        onlyBefore(orderRecords[id].endTime)
        inState(id, State.Created)
    {
        orderRecords[id].deliverHash = deliverHash;
        orderRecords[id].state = State.Delivered;
    }

    function confirmDeliver(uint id)
        public
        onlyBuyer(id)
        onlyBefore(orderRecords[id].endTime)
        inState(id, State.Delivered)
    {
        orderRecords[id].state = State.Confirmed;
        finalizeOrder(id, orderRecords[id].sellerAddress);
    }

    function sellerClaimTimedOut(uint id)
        public
        onlySeller(id)
        inState(id, State.Delivered)
        onlyAfter(orderRecords[id].endTime)
    {
        finalizeOrder(id, orderRecords[id].sellerAddress);
    }

    function sellerRateProxy(uint id, uint rate)
        public
        onlySeller(id)
        inState(id, State.Finished)
    {
        require(rate >= 0 && rate <= 100);
        orderRecords[id].state = State.Rated;
        proxyCredits[orderRecords[id].proxyAddress] = proxyCredits[orderRecords[id].proxyAddress] + rate;
        proxyCredits[orderRecords[id].secondaryProxyAddress] = proxyCredits[orderRecords[id].secondaryProxyAddress] + rate;
    }

    function buyerRateProxy(uint id, uint rate)
        public
        onlyBuyer(id)
        inState(id, State.Finished)
    {
        require(rate >= 0 && rate <= 100);
        orderRecords[id].state = State.Rated;
        proxyCredits[orderRecords[id].proxyAddress] = proxyCredits[orderRecords[id].proxyAddress] + rate;
        proxyCredits[orderRecords[id].secondaryProxyAddress] = proxyCredits[orderRecords[id].secondaryProxyAddress] + rate;
    }

    function finalizeOrder(uint id, address beneficiary)
        private
    {
        orderRecords[id].state = State.Finished;
        uint payProxy = orderRecords[id].proxyFee;
        uint payBeneficiary = orderRecords[id].offeredPrice - payProxy * 2;
        beneficiary.transfer(payBeneficiary);
	    // FIXME
	// this logic is wrong.
        orderRecords[id].proxyAddress.transfer(payProxy);
        orderRecords[id].secondaryProxyAddress.transfer(payProxy);
    }

}
