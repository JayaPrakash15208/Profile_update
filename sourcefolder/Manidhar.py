mobileDictionary = {
    'APPLE':{'RAM':12,'ROM':256,'DISPLAY':'AMOLED','BATTERY':5000,'PRICE':80000},
    'SAMSUNG':{'RAM':8,'ROM':128,'DISPLAY':'OLED','BATTERY':3000,'PRICE':30000},
    'VIVO':{'RAM':8,'ROM':64,'DISPLAY':'LED','BATTERY':5500,'PRICE':27000},
    'REDMI':{'RAM':10,'ROM':256,'DISPLAY':'QLED','BATTERY':4800,'PRICE':50000},
    'OPPO':{'RAM':14,'ROM':512,'DISPLAY':'AMOLED','BATTERY':5100,'PRICE':25000},
    'IQOO':{'RAM':14,'ROM':212,'DISPLAY':'SUPER AMOLED','BATTERY':5100,'PRICE':30000}
}

AdditionalPhone='y'
# print(mobileDictionary)
while AdditionalPhone == 'y': 
    print(f'I have below phones')
    for key in mobileDictionary.keys():
        print(key)

    mobile = input("Please select the mobile from the list:\t")
    if mobile.upper() in mobileDictionary:

        mobileData= mobileDictionary[mobile.upper()]
        for mobileSpec in mobileData.keys():
            print(f'{mobileSpec} : {mobileData[mobileSpec]}')
    else:
        print("Please visist other store, we doesn't have the phone you required")

    AdditionalPhone=input(f'You want to see any additonal phones y/n:\t')



