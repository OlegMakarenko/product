import configparser
from pathlib import Path


def prepare_shoestring_configuration(directory, node_features, services_nodewatch='', **node_kwargs):
	"""Prepares a shoestring configuration file in the specified directory."""

	parser = configparser.ConfigParser()
	parser.read(Path('tests/resources/sai.shoestring.ini').absolute())

	parser['services']['nodewatch'] = str(services_nodewatch)

	node_features_str = str(node_features)
	parser['node']['features'] = node_features_str[node_features_str.index('.') + 1:]
	parser['node']['caPassword'] = f'pass:{node_kwargs.get("ca_password")}' if 'ca_password' in node_kwargs else ''

	if 'api_https' in node_kwargs:
		parser['node']['apiHttps'] = 'true' if node_kwargs.get('api_https') else 'as-false-as-can-get'

	parser['node']['caCommonName'] = node_kwargs.get('ca_common_name', 'my CA name')
	parser['node']['nodeCommonName'] = node_kwargs.get('node_common_name', 'my Node name')

	output_filepath = Path(directory) / 'sai.shoestring.ini'
	with open(output_filepath, 'wt', encoding='utf8') as outfile:
		parser.write(outfile)

	return output_filepath