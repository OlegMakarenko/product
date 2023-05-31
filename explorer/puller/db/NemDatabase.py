from db.DatabaseConnection import DatabaseConnection


class NemDatabase(DatabaseConnection):
	"""Database containing Nem blockchain data."""

	def create_tables(self):
		"""Creates blocks database tables."""

		cursor = self.connection.cursor()
		cursor.execute('''CREATE TABLE IF NOT EXISTS blocks (
			height integer NOT NULL,
			timestamp timestamp NOT NULL,
			totalFees integer DEFAULT 0,
			totalTransactions integer DEFAULT 0,
			difficulty bigInt NOT NULL,
			hash VARCHAR(64) NOT NULL,
			harvester VARCHAR(40) NOT NULL
		)''')

		# Create transactions table
		cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
			hash VARCHAR(64) NOT NULL,
			height bigint NOT NULL,
			sender VARCHAR(40),
			fee bigint NOT NULL,
			timestamp timestamp NOT NULL,
			deadline timestamp NOT NULL,
			signature VARCHAR(128) NOT NULL,
			version VARCHAR(10) NOT NULL,
			type VARCHAR(20) NOT NULL,
			isApostille boolean,
			isMosaicTransfer boolean,
			isAggregate boolean,
			PRIMARY KEY (hash)
		)''')

		# Create transfer transactions table
		cursor.execute('''CREATE TABLE IF NOT EXISTS transfer_transactions (
			hash VARCHAR(64) NOT NULL,
			amount bigint NOT NULL,
			recipient VARCHAR(40) NOT NULL,
			messagePayload VARCHAR(1024),
			messageType integer,
			PRIMARY KEY (hash),
			FOREIGN KEY (hash) REFERENCES transactions(hash) ON DELETE CASCADE
		)''')

		self.connection.commit()

	def insert_block(self, block):
		"""Adds block height into table."""

		cursor = self.connection.cursor()
		cursor.execute('''INSERT INTO blocks VALUES (%s, %s, %s, %s, %s, %s, %s)''', (
			block['height'],
			block['timestamp'],
			block['totalFees'],
			block['totalTransactions'],
			block['difficulty'],
			block['hash'],
			block['signer']
		))
		self.connection.commit()

	def insert_transactions(self, transactions):
		"""Adds transactions into transactions table"""

		print(f"Inserting transactions into database... {len(transactions)}")

		cursor = self.connection.cursor()

		cursor.executemany(
			'''INSERT INTO transactions VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
			transactions
		)

		self.connection.commit()

	def insert_transactions_transfer(self, transfer):
		"""Adds transfer into transfer_transactions table"""

		cursor = self.connection.cursor()

		print(transfer)

		cursor.executemany(
			'''INSERT INTO transfer_transactions VALUES (%s, %s, %s, %s, %s)''',
			transfer
		)

		self.connection.commit()

	def get_current_height(self):
		"""Gets current height from database"""

		cursor = self.connection.cursor()
		cursor.execute('''SELECT MAX(height) FROM blocks''')
		results = cursor.fetchone()
		return 0 if results[0] is None else results[0]
