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
		type
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


class TransferTransaction:
	def __init__(self, hash, amount, mosaics, recipient, message, is_apostille):
		"""Create TransferTransaction model."""

		self.hash = hash
		self.amount = amount
		self.mosaics = mosaics
		self.recipient = recipient
		self.message = message
		self.is_apostille = is_apostille
