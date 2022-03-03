import argparse
import asyncio
import sqlite3
from pathlib import Path

from aiolimiter import AsyncLimiter

from puller.client.NemClient import NemClient
from puller.db.BalancesDatabase import BalancesDatabase
from puller.db.InProgressOptinDatabase import InProgressOptinDatabase
from puller.db.MultisigDatabase import MultisigDatabase

SNAPSHOT_HEIGHT = 3105500


def get_addresses(filename):
	with sqlite3.connect(f'file:{filename}?mode=ro', uri=True) as connection:
		in_progress_database = InProgressOptinDatabase(connection)

		return [optin_request.address for optin_request in in_progress_database.requests]


async def populate_balances(connection, client, addresses):
	database = BalancesDatabase(connection)
	database.create_tables()

	limiter = AsyncLimiter(20, 1.0)

	async def get_state(address):
		async with limiter:
			account_balance = await client.historical_balance(address, SNAPSHOT_HEIGHT)
			database.add_account_balance(*account_balance)

			print('.', end='', flush=True)

	tasks = list(map(get_state, addresses))
	await asyncio.gather(*tasks)


async def populate_multisig(connection, client, addresses):
	database = MultisigDatabase(connection)
	database.create_tables()

	limiter = AsyncLimiter(20, 1.0)

	async def get_state(address):
		async with limiter:
			account = await client.account(address)
			database.insert_if_multisig(account)

			print('.', end='', flush=True)

	tasks = list(map(get_state, addresses))
	await asyncio.gather(*tasks)


async def main():
	parser = argparse.ArgumentParser(description='download post optin account states')
	parser.add_argument('--node', help='NEM node url', default='http://superalice.nemmain.net:7890')
	parser.add_argument('--database-directory', help='output database directory', default='_temp')
	args = parser.parse_args()

	client = NemClient(args.node)
	addresses = set(get_addresses(Path(args.database_directory) / 'in_progress.db'))

	print('populating balances...')
	with sqlite3.connect(Path(args.database_directory) / 'balances.db') as connection:
		await populate_balances(connection, client, addresses)

	print('populating multisig...')
	with sqlite3.connect(Path(args.database_directory) / 'multisig.db') as connection:
		await populate_multisig(connection, client, addresses)

	print('*** *** ***')
	print(f'==> accounts processed: {len(addresses)}')


asyncio.run(main())
