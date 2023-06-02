from db.DatabaseConnection import DatabaseConnection
from zenlog import log

class NemDatabase(DatabaseConnection):
	"""Database containing Nem blockchain data."""

	def create_tables(self):
		"""Creates blocks database tables."""

		cursor = self.connection.cursor()

		# Create blocks table
		cursor.execute('''CREATE TABLE IF NOT EXISTS blocks (
			height bigint NOT NULL,
			timestamp timestamp NOT NULL,
			totalFees bigint DEFAULT 0,
			totalTransactions integer DEFAULT 0,
			difficulty bigInt NOT NULL,
			hash VARCHAR(64) NOT NULL,
			harvester VARCHAR(40) NOT NULL
		)''')

		# Create transactions table
		cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
			hash varchar(64) NOT NULL,
			height bigint NOT NULL,
			sender varchar(40),
			fee bigint NOT NULL,
			timestamp timestamp NOT NULL,
			deadline timestamp NOT NULL,
			signature varchar(128) NOT NULL,
			version varchar(10) NOT NULL,
			type varchar(20) NOT NULL,
			PRIMARY KEY (hash)
		)''')

		# Create transfer transactions table
		cursor.execute('''CREATE TABLE IF NOT EXISTS transfer_transactions (
			hash varchar(64) NOT NULL,
			amount bigint NOT NULL,
			mosaics json,
			recipient varchar(40) NOT NULL,
			message json,
			isApostille boolean DEFAULT false,
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

		log.info(f"Inserting transactions into database... {len(transactions)}")

		cursor = self.connection.cursor()

		cursor.executemany(
			'''INSERT INTO transactions VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''',
			list((
				tx.hash,
				tx.height,
				tx.sender,
				tx.fee,
				tx.timestamp,
				tx.deadline,
				tx.signature,
				tx.version,
				tx.type
			) for tx in transactions)
		)

		self.connection.commit()

	def insert_transactions_transfer(self, transfer_transactions):
		"""Adds transfer into transfer_transactions table"""

		log.info(f"Inserting transfer transactions into database... {len(transfer_transactions)}")

		cursor = self.connection.cursor()

		cursor.executemany(
			'''INSERT INTO transfer_transactions VALUES (%s, %s, %s, %s, %s, %s)''',
			list((
				t.hash,
				t.amount,
				t.mosaics,
				t.recipient,
				t.message,
				t.is_apostille
			) for t in transfer_transactions)
		)

		self.connection.commit()

	def get_current_height(self):
		"""Gets current height from database"""

		cursor = self.connection.cursor()
		cursor.execute('''SELECT MAX(height) FROM blocks''')
		results = cursor.fetchone()
		return 0 if results[0] is None else results[0]
