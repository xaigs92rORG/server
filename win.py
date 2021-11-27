import aiohttp, asyncio, argparse

parser = argparse.ArgumentParser()
parser.add_argument('password')
args = parser.parse_args()

subscription = '9046396e-e215-4cc5-9eb7-e25370140233'

async def main():
    async with aiohttp.ClientSession() as session:
        async with session.post(f'https://login.microsoftonline.com/{args.tenantid}/oauth2/token', data={'grant_type':'client_credentials', 'client_id':args.clientid, 'client_secret':args.clientsecret, 'resource':'https://management.azure.com/'}) as response:
            token = (await response.json()).get('access_token')
        async with session.put(f'https://management.azure.com/subscriptions/{subscription}/resourceGroups/machine/providers/Microsoft.Compute/virtualMachines/win?api-version=2021-07-01', headers={'authorization':f'Bearer {token}'}, json={'location':'westus', 'properties':{'hardwareProfile':{'vmSize':'Standard_B1s'}, 'osProfile':{'adminUsername':'ubuntu', 'computerName':'win', 'adminPassword':args.password}, 'storageProfile':{'imageReference':{'sku':'2022-datacenter-azure-edition-core-smalldisk', 'publisher':'MicrosoftWindowsServer', 'version':'latest', 'offer':'WindowsServer'}, 'osDisk':{'diskSizeGB':64, 'createOption':'FromImage'}}, 'networkProfile':{'networkInterfaces':[{'id':'/subscriptions/9046396e-e215-4cc5-9eb7-e25370140233/resourceGroups/machine/providers/Microsoft.Network/networkInterfaces/win'}]}, 'availabilitySet':{'id':'/subscriptions/9046396e-e215-4cc5-9eb7-e25370140233/resourceGroups/machine/providers/Microsoft.Compute/availabilitySets/MACHINE'}}}) as machine:
                if machine.status == 201:
                    while True:
                        await asyncio.sleep(int(machine.headers.get('retry-after')))
                        async with session.get(machine.headers.get('azure-asyncOperation'), headers={'authorization':f'Bearer {token}'}) as _:
                            if (await _.json()).get('status') == 'Succeeded': break

asyncio.run(main())