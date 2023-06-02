import argparse
import binascii
import json

from asyncio import run

from symbolchain.CryptoTypes import PublicKey
from symbolchain.facade.NemFacade import NemFacade
from zenlog import log

from facade.NemPullerFacade import NemPullerFacade
from model.Block import Block
from model.Transaction import Transaction, TransferTransaction

APOSTILLE_ADDRESS = 'NCZSJHLTIMESERVBVKOW6US64YDZG2PFGQCSV23J'


def parse_args():
	"""Parse command line arguments."""

	parser = argparse.ArgumentParser(description='sync blocks from network')
	parser.add_argument('--nem-node', help='NEM node(local) url', default='http://localhost:7890')
	parser.add_argument('--db-config', help='database config file *.ini', default='config.ini')
	return parser.parse_args()

def _process_transaction(databases, nem_facade, block_transaction):
	transactions_list = []
	transfer_transactions = []

	height = block_transaction['height']

	for tx in block_transaction['txes']:
		transaction = tx['tx']
		transaction_hash = tx['hash']
		save_transaction = Transaction(
			hash=tx['hash'],
			height=height,
			sender=str(nem_facade.network.public_key_to_address(PublicKey(transaction['signer']))),
			fee=transaction['fee'],
			timestamp=Block.convert_timestamp_to_datetime(nem_facade, transaction['timeStamp']),
			deadline=Block.convert_timestamp_to_datetime(nem_facade, transaction['deadline']),
			signature=transaction['signature'],
			version=transaction['version'],
			type=transaction['type']
		)

		# process TransferTransaction
		if 257 == transaction['type']:
			is_apostille = False

			if transaction['recipient'] == APOSTILLE_ADDRESS and transaction['message'] and transaction['message']['type'] and transaction['message']['type'] == 1:
				message = binascii.unhexlify(transaction['message']['payload'])
				if message.startswith(b'HEX:'):
					is_apostille = True

			print(transaction['mosaics'] if 'mosaics' in transaction else None)
			save_transfer_transaction = TransferTransaction(
				hash=transaction_hash,
				amount=transaction['amount'] if 'amount' in transaction else 0,
				mosaics = json.dumps(transaction['mosaics']) if 'mosaics' in transaction else None,
				recipient= transaction['recipient'] if 'recipient' in transaction else None,
				message= json.dumps(transaction['message']) if 'message' in transaction else None,
				is_apostille= is_apostille
			)

			transfer_transactions.append(save_transfer_transaction)

		transactions_list.append(save_transaction)

	databases.insert_transactions(transactions_list)
	databases.insert_transactions_transfer(transfer_transactions)


async def save_nemesis_block(nem_client, databases, nem_facade):
	"""Save the Nemesis block."""

	block = await nem_client.get_block(1)

	# process Block
	save_block = Block(
		block['height'],
		Block.convert_timestamp_to_datetime(nem_facade, block['timeStamp']),
		0,
		len(block['transactions']),
		0,
		'#',
		str(nem_facade.network.public_key_to_address(PublicKey(block['signer'])))
	)

	databases.insert_block(save_block.to_dict())

	# process Transaction
	_process_transaction(databases, nem_facade, {
		'txes': [{
			'tx': tx,
			'hash': f'#NemesisBlock# {index}'
		} for index, tx in enumerate(block['transactions'], start=1)
		],
		'height': block['height']
	})


async def sync_blocks(nem_client, databases, db_height, chain_height, nem_facade):
	"""Sync network blocks in the database."""

	# sync network blocks in database
	while chain_height > db_height:

		blocks = await nem_client.get_blocks_after(db_height)

		for block in blocks['data']:
			save_block = Block.from_nem_block_data(block, nem_facade)
			databases.insert_block(save_block.to_dict())

			# process Transaction
			_process_transaction(databases, nem_facade, {
				'txes': block['txes'],
				'height': block['block']['height']
			})

		db_height = blocks['data'][-1]['block']['height']

		log.info(f'added block from height {blocks["data"][0]["block"]["height"]} - {blocks["data"][-1]["block"]["height"]}')


async def main():
	args = parse_args()

	facade = NemPullerFacade(args.nem_node, args.db_config)

	nem_client = facade.client()
	nem_databases = facade.database

	nem_network = await nem_client.node_network()
	nem_facade = NemFacade(nem_network.name)

	log.info(f'Node URL: {args.nem_node}')
	log.info(f'Syncing with network {nem_network}')

	with nem_databases() as databases:
		databases.create_tables()

		db_height = databases.get_current_height()
		log.info(f'current database height: {db_height}')
		chain_height = await nem_client.height()

		# save Nemesis Block
		if db_height == 0:
			await save_nemesis_block(nem_client, databases, nem_facade)
			db_height = 1

		# sync network blocks in database
		await sync_blocks(nem_client, databases, db_height, chain_height, nem_facade)

		log.info('Database is up to date')

if __name__ == '__main__':
	run(main())
