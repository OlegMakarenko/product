import tempfile
from pathlib import Path

from symbolchain.CryptoTypes import PrivateKey
from symbolchain.PrivateKeyStorage import PrivateKeyStorage

from shoestring.__main__ import main
from shoestring.internal.NodeFeatures import NodeFeatures
from shoestring.internal.Preparer import Preparer
from shoestring.internal.ShoestringConfiguration import parse_shoestring_configuration

from ..test.CertificateTestUtils import assert_certificate_properties, create_openssl_executor
from ..test.ConfigurationTestUtils import prepare_shoestring_configuration

# pylint: disable=invalid-name


# region node certificate renewal only

async def _assert_can_renew_node_certificate(ca_password=None):
	# Arrange:
	with tempfile.TemporaryDirectory() as output_directory:
		config_filepath = prepare_shoestring_configuration(
			output_directory,
			NodeFeatures.PEER,
			ca_password=ca_password,
			ca_common_name='ORIGINAL CA CN',
			node_common_name='NEW NODE CN')
		preparer = Preparer(output_directory, parse_shoestring_configuration(config_filepath))

		# - generate CA private key pem file
		ca_private_key = PrivateKey.random()
		private_key_storage = PrivateKeyStorage(output_directory, ca_password)
		private_key_storage.save('ca.key', ca_private_key)

		# - generate initial set of certificates
		#   in order for node certificate to be verifiable, CA must have same issuer and subject
		ca_key_path = Path(output_directory) / 'ca.key.pem'
		preparer.directories.certificates.mkdir(parents=True)
		preparer.generate_certificates(ca_key_path, 'ORIGINAL CA CN', 'ORIGINAL NODE CN', require_ca=True)

		# - save last modified times
		ca_certificate_path = preparer.directories.certificates / 'ca.crt.pem'
		ca_certificate_last_modified_time = ca_certificate_path.stat().st_mtime

		node_certificate_path = preparer.directories.certificates / 'node.crt.pem'
		node_certificate_last_modified_time = node_certificate_path.stat().st_mtime

		# Sanity:
		assert_certificate_properties(node_certificate_path, 'ORIGINAL CA CN', 'ORIGINAL NODE CN', 375)
		assert_certificate_properties(ca_certificate_path, 'ORIGINAL CA CN', 'ORIGINAL CA CN', 20 * 365)

		# Act:
		await main([
			'renew-certificates',
			'--config', str(config_filepath),
			'--directory', output_directory,
			'--ca-key-path', str(ca_key_path)
		])

		# Assert: node certificate is regenerated (subject changed)
		assert_certificate_properties(node_certificate_path, 'ORIGINAL CA CN', 'NEW NODE CN', 375)
		create_openssl_executor().dispatch(['verify', '-CAfile', ca_certificate_path, node_certificate_path])
		assert node_certificate_last_modified_time != node_certificate_path.stat().st_mtime

		# - ca certificate is not regenerated
		assert_certificate_properties(ca_certificate_path, 'ORIGINAL CA CN', 'ORIGINAL CA CN', 20 * 365)
		create_openssl_executor().dispatch(['verify', '-CAfile', ca_certificate_path, ca_certificate_path])
		assert ca_certificate_last_modified_time == ca_certificate_path.stat().st_mtime


async def test_can_renew_node_certificate():
	await _assert_can_renew_node_certificate()


async def test_can_renew_node_certificate_with_ca_password():
	await _assert_can_renew_node_certificate('abc')

# endregion


# region CA and node certificates renewal

async def _assert_can_renew_ca_and_node_certificates(ca_password=None):
	# Arrange:
	with tempfile.TemporaryDirectory() as output_directory:
		config_filepath = prepare_shoestring_configuration(
			output_directory,
			NodeFeatures.PEER,
			ca_password=ca_password,
			ca_common_name='NEW CA CN',
			node_common_name='NEW NODE CN')
		preparer = Preparer(output_directory, parse_shoestring_configuration(config_filepath))

		# - generate CA private key pem file
		ca_private_key = PrivateKey.random()
		private_key_storage = PrivateKeyStorage(output_directory, ca_password)
		private_key_storage.save('ca.key', ca_private_key)

		# - generate initial set of certificates
		ca_key_path = Path(output_directory) / 'ca.key.pem'
		preparer.directories.certificates.mkdir(parents=True)
		preparer.generate_certificates(ca_key_path, 'ORIGINAL CA CN', 'ORIGINAL NODE CN', require_ca=True)

		# - save last modified times
		ca_certificate_path = preparer.directories.certificates / 'ca.crt.pem'
		ca_certificate_last_modified_time = ca_certificate_path.stat().st_mtime

		node_certificate_path = preparer.directories.certificates / 'node.crt.pem'
		node_certificate_last_modified_time = node_certificate_path.stat().st_mtime

		# Sanity:
		assert_certificate_properties(node_certificate_path, 'ORIGINAL CA CN', 'ORIGINAL NODE CN', 375)
		assert_certificate_properties(ca_certificate_path, 'ORIGINAL CA CN', 'ORIGINAL CA CN', 20 * 365)

		# Act:
		await main([
			'renew-certificates',
			'--config', str(config_filepath),
			'--directory', output_directory,
			'--ca-key-path', str(ca_key_path),
			'--renew-ca'
		])

		# Assert: node certificate is regenerated (subject changed)
		assert_certificate_properties(node_certificate_path, 'NEW CA CN', 'NEW NODE CN', 375)
		create_openssl_executor().dispatch(['verify', '-CAfile', ca_certificate_path, node_certificate_path])
		assert node_certificate_last_modified_time != node_certificate_path.stat().st_mtime

		# - ca certificate is regenerated (subject changed)
		assert_certificate_properties(ca_certificate_path, 'NEW CA CN', 'NEW CA CN', 20 * 365)
		create_openssl_executor().dispatch(['verify', '-CAfile', ca_certificate_path, ca_certificate_path])
		assert ca_certificate_last_modified_time != ca_certificate_path.stat().st_mtime


async def test_can_renew_ca_and_node_certificates():
	await _assert_can_renew_ca_and_node_certificates()


async def test_can_renew_ca_and_node_certificates_with_ca_password():
	await _assert_can_renew_ca_and_node_certificates('abc')

# endregion