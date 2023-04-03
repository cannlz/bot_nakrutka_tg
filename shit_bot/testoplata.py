from yoomoney import Authorize
from yoomoney import Client
from yoomoney import Quickpay
import os

#my_secret = os.environ['bot_token_test']
token = "4100118083812502.AB0612C4D73A4C6534F57AD11E6B8CF2DDE4D1F45B87E7CFAC58249B0EA65FEDDBBF257AD1227AA5448ACC2B5148C7DBC445C83C6809C9F419A17ED33F116B45BEC77ECEC62409CC39B8238D358E37DABD8CB48B2DA22FE503D1CF6B5CFDC909002677C40C68C8005FDBCB56F60B01C31482A729874CCAB408733037A36178CA"
def auttorize_yoomoney():
    client = Client(token)
    user = client.account_info()
    print("Account number:", user.account)
    print("Account balance:", user.balance)
    print("Account currency code in ISO 4217 format:", user.currency)
    print("Account status:", user.account_status)
    print("Account type:", user.account_type)
    print("Extended balance information:")
    for pair in vars(user.balance_details):
        print("\t-->", pair, ":", vars(user.balance_details).get(pair))
    print("Information about linked bank cards:")
    cards = user.cards_linked
    if len(cards) != 0:
        for card in cards:
            print(card.pan_fragment, " - ", card.type)
    else:
        print("No card is linked to the account")


def pay(labelGen, sumGen):
    quickpay = Quickpay(
            receiver="4100118083812502",
            quickpay_form="shop",
            targets="Sponsor this project",
            paymentType="SB",
            label=labelGen,
            sum=sumGen,
            )
    #print(quickpay.base_url)
    #print(quickpay.redirected_url)
    return quickpay.redirected_url

def check_pay(labelGen):
    client = Client(token)
    history = client.operation_history(label=labelGen)
    #print("List of operations:")
    #print("Next page starts with: ", history.next_record)
    for operation in history.operations:
        if operation.label == labelGen:
            print("Operation:",operation.operation_id)
            print("\tStatus     -->", operation.status) #
            print("\tDatetime   -->", operation.datetime) #
            print("\tAmount     -->", operation.amount) #
            print("\tLabel      -->", operation.label) #
            print("\tType       -->", operation.type) #
            return(operation.status, operation.amount)


def check_pay_test(labelGen):
    client = Client(token)
    history = client.operation_history()
    #print("List of operations:")
    #print("Next page starts with: ", history.next_record)
    for operation in history.operations:
        if operation.type == "deposition" and operation.label == labelGen:
            print("Operation:",operation.operation_id)
            print("\tStatus     -->", operation.status) #
            print("\tDatetime   -->", operation.datetime) #
            print("\tAmount     -->", operation.amount) #
            print("\tLabel      -->", operation.label) #
            print("\tType       -->", operation.type) #
            return(operation.status, operation.amount)

#check_pay_test()
#auttorize_yoomoney()
#pay()
#check_pay()