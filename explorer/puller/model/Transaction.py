class Transaction:
	def __init__(
		self,
		hash,
		height,
		sender,
		fee,
		timestamp,
		deadline,
		signature,
		version,
		type,
		is_apostille,
		is_mosaic_transfer,
		is_aggregate
	):
		"""Create Transaction model."""

		# pylint: disable=too-many-arguments

		self.hash = hash
		self.height = height
		self.sender = sender
		self.fee = fee
		self.timestamp = timestamp
		self.deadline = deadline
		self.signature = signature
		self.version = version
		self.type = type
		self.is_apostille = is_apostille
		self.is_mosaic_transfer = is_mosaic_transfer
		self.is_aggregate = is_aggregate


class TransferTransaction:
	def __init__(self, hash, amount, recipient, message_payload, message_type):
		"""Create TransferTransaction model."""

		self.hash = hash
		self.amount = amount
		self.recipient = recipient
		self.message_payload = message_payload
		self.message_type = message_type
