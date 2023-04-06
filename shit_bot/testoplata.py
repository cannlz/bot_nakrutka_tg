from yoomoney import Authorize
from yoomoney import Client
from yoomoney import Quickpay
import os

#my_secret = os.environ['bot_token_test']
token = "4100118083812502.7C9295DEB50F5ED1F7F3E7B8BC36DC423EA874DC4F9922098193898A5D0E1E74A92435A3A6B815F4A43D49666BFA0D455D8830B64BA68BF3154958881BF393885D5714DC095C0469A30E0CA04E863D3AAE4851F72C9F9653F9FD76CA14D76DB633270BDE8D081A8F487CB4BAC1C48AC2F5210A2C353C69452ADE6A3AD4E08F4D"
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