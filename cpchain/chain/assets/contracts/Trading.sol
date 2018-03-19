pragma solidity ^0.4.0;

/*
    A Trading Contract for basic transactions in CPChain.
*/
contract Trading {

    enum State {
        Created,
        Delivered,
        Confirmed,
        Finished,
        Disputed,
        Withdrawn
    }

    struct TransInfo {
        bytes32 descHash;
        address buyerAddress;
        address sellerAddress;
        address proxyAddress;
        address backupProxyAddress;
        uint offeredPrice;
        uint payProxyRatio; // ratio / 10000 = percentage
        bytes32 deliverHash;
        uint endTime;
        State state;
    }

    uint public timeAllowed = 600; // Unit is second
    uint public numTrans = 0;
    // TODO let records to be public or only let relevant address to be a accessible
    mapping(uint => TransInfo) public transRecords;

    mapping(address => uint) public proxyCredits;

    // Security Checks
    modifier onlyBefore(uint time) { require(now < time); _; }
    modifier onlyAfter(uint time) { require(now > time); _; }
    modifier onlyBuyer(uint id) { require(msg.sender == transRecords[id].buyerAddress); _; }
    modifier onlySeller(uint id) { require(msg.sender == transRecords[id].sellerAddress); _; }
    modifier onlyProxy(uint id) {
        require(
            msg.sender == transRecords[id].proxyAddress ||
            msg.sender == transRecords[id].backupProxyAddress
        );
        _;
    }
    modifier inState(uint id, State _state) { require(transRecords[id].state == _state); _; }

    function Trading() public {
        // Maybe useful in the future.
    }

    function() payable {
        // Maybe useful in the future.
    }

    event TransInitiated(
        address indexed from,
        uint transId,
        uint value
    );

    function createTransaction(
        bytes32 descHash,
        address seller,
        address proxy,
        address backupProxy,
        uint payProxyRatio
    )
        public
        payable
    {
        uint thisID = numTrans++;
        transRecords[thisID] = TransInfo({
            descHash: descHash,
            buyerAddress: msg.sender,
            sellerAddress: seller,
            proxyAddress: proxy,
            backupProxyAddress: backupProxy,
            deliverHash: bytes32(0),
            offeredPrice: msg.value,
            payProxyRatio: payProxyRatio,
            endTime: now + timeAllowed,
            state: State.Created
        });
        TransInitiated(msg.sender, thisID, msg.value);
    }

    function buyerWithdraw(uint id)
        public
        onlyBuyer(id)
        onlyBefore(transRecords[id].endTime)
        inState(id, State.Created)
    {
        transRecords[id].state = State.Withdrawn;
        transRecords[id].buyerAddress.transfer(transRecords[id].offeredPrice);
    }

    function buyerDispute(uint id)
        public
        onlyBuyer(id)
        onlyBefore(transRecords[id].endTime)
        inState(id, State.Delivered)
    {
        transRecords[id].state = State.Disputed;
    }

    function proxyJudge(uint id, bool decision)
        public
        onlyProxy(id)
        onlyBefore(transRecords[id].endTime)
        inState(id, State.Disputed)
    {
        if (decision == true)
            finalizeTransaction(id, transRecords[id].sellerAddress);
        else
            finalizeTransaction(id, transRecords[id].buyerAddress);
    }

    function deliverMsg(bytes32 deliverHash, uint id)
        public
        onlySeller(id)
        onlyBefore(transRecords[id].endTime)
        inState(id, State.Created)
    {
        transRecords[id].deliverHash = deliverHash;
        transRecords[id].state = State.Delivered;
    }

    function confirmDeliver(uint id)
        public
        onlyBuyer(id)
        onlyBefore(transRecords[id].endTime)
        inState(id, State.Delivered)
    {
        transRecords[id].state = State.Confirmed;
        finalizeTransaction(id, transRecords[id].sellerAddress);
    }

    function sellerClaimTimedOut(uint id)
        public
        onlySeller(id)
        inState(id, State.Delivered)
        onlyAfter(transRecords[id].endTime)
    {
        finalizeTransaction(id, transRecords[id].sellerAddress);
    }

    function finalizeTransaction(uint id, address beneficiary)
        private
    {
        transRecords[id].state = State.Finished;
        uint payProxy = transRecords[id].offeredPrice * (transRecords[id].payProxyRatio / 100);
        uint payBeneficiary = transRecords[id].offeredPrice - payProxy * 2;
        beneficiary.transfer(payBeneficiary);
        transRecords[id].proxyAddress.transfer(payProxy);
        transRecords[id].backupProxyAddress.transfer(payProxy);
    }

}

