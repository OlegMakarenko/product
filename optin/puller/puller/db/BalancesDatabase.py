class BalancesDatabase:
	"""Database containing snapshot account balances."""

	def __init__(self, connection):
		"""Creates a database around a database connection."""

		self.connection = connection

	def create_tables(self):
		"""Creates balances database tables."""

		cursor = self.connection.cursor()
		cursor.execute('''CREATE TABLE IF NOT EXISTS snapshot_balances (
			address blob UNIQUE,
			balance integer
		)''')

	def add_account_balance(self, address, balance):
		"""Adds an account to the balances table."""

		cursor = self.connection.cursor()
		cursor.execute('''INSERT INTO snapshot_balances VALUES (?, ?)''', (address.bytes, balance))

	def lookup_balance(self, address):
		"""Gets the balance for the specified address."""

		cursor = self.connection.cursor()
		cursor.execute('''SELECT balance FROM snapshot_balances WHERE address = ?''', (address.bytes,))
		return cursor.fetchone()[0]