import json
from binascii import hexlify, unhexlify
from collections import namedtuple

from symbolchain.CryptoTypes import Hash256
from symbolchain.nem.Network import Address as NemAddress
from symbolchain.sc import MosaicId
from symbolchain.symbol.Network import Network
from symbolchain.symbol.NetworkTimestamp import NetworkTimestamp

from .BasicClient import BasicClient

OptInTransactionInfo = namedtuple('OptInTransactionInfo', ['address', 'transaction_hash'])


class SymbolClient(BasicClient):
	"""Async client for connecting to a NEM node."""

	async def is_known_address(self, address):
		"""Determines if specified address is known to the network."""

		url_path = f'accounts/{address}'
		account = await self.get(url_path, None)
		return 'account' in account

	async def height(self):
		"""Gets current blockchain height."""

		return await self.get('chain/info', 'height')

	async def finalized_height(self):
		"""Gets current blockchain finalized height."""

		return (await self.get('chain/info', 'latestFinalizedBlock'))['height']

	async def announce(self, transaction_buffer):
		"""Announces serialized transaction."""

		request = {'payload': hexlify(transaction_buffer).decode('utf8').upper()}
		return await self.put('transactions', request)

	async def node_time(self):
		"""Gets node time."""

		timestamps = await self.get('node/time', 'communicationTimestamps')
		return NetworkTimestamp(int(timestamps['receiveTimestamp']))

	async def node_network(self):
		"""Gets node network."""

		if not self.network:
			network_identifier = await self.get('node/info', 'networkIdentifier')
			self.network = Network.TESTNET if 152 == network_identifier else Network.MAINNET

		return self.network

	async def network_currency(self):
		"""Gets network currency."""

		chain_info = await self.get('network/properties', 'chain')
		return MosaicId(int(chain_info['currencyMosaicId'].replace('\'', ''), 0))

	async def transaction_statuses(self, transaction_hashes):
		"""Gets the statuses of the specified transactions."""

		request = {'hashes': [str(transaction_hash) for transaction_hash in transaction_hashes]}
		return await self.post('transactionStatus', request)

	async def find_optin_transactions(self, optin_signer_public_key, address):
		"""Finds optin transactions sent to the specified address."""

		url_path = f'transactions/confirmed?signerPublicKey={optin_signer_public_key}&recipientAddress={address}&embedded=true'
		transactions = await self.get(url_path, 'data')
		return [
			OptInTransactionInfo(
				NemAddress(json.loads(unhexlify(transaction['transaction']['message'][2:]))['nisAddress']),
				Hash256(transaction['meta']['aggregateHash']))
			for transaction in transactions
		]


async def filter_finalized_transactions(client, transaction_hashes):
	"""Filters transaction hashes and returns only finalized ones."""

	finalized_height = await client.finalized_height()
	transaction_statuses = await client.transaction_statuses(transaction_hashes)

	finalized_transaction_hashes = []
	for transaction_status in transaction_statuses:
		if 'confirmed' == transaction_status['group'] and int(transaction_status['height']) <= finalized_height:
			finalized_transaction_hashes.append(Hash256(transaction_status['hash']))

	return finalized_transaction_hashes