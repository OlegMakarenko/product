class Screens:
	def __init__(self, navbar):
		self.navbar = navbar  # added so that screens can access and modify it directly
		self.ordered = []
		self.current_id = 0
		# TODO: this needs to become property to handle allowed_list filtering
		self.ordered_group_names = []
		self.group_name = []

		self.allowed_list = None
		self.chain = []

	def add(self, screen_group_name, descriptor):
		if screen_group_name not in self.ordered_group_names:
			self.ordered_group_names.append(screen_group_name)

		self.group_name.append(screen_group_name)
		self.ordered.append(descriptor)

	def get(self, screen_id):
		index = [screen.screen_id for screen in self.ordered].index(screen_id)
		return self.ordered[index].accessor

	def set_list(self, list):
		self.allowed_list = list

	@property
	def current(self):
		return self.ordered[self.current_id]

	def has_previous(self):
		return bool(self.chain)

	def previous(self):
		if not self.chain:
			return self.current

		self.current_id = self.chain.pop()
		return self.current

	def next(self):
		original_id = self.current_id

		next_id = self.current_id + 1
		while next_id != len(self.ordered):
			if self.ordered[next_id].screen_id in self.allowed_list and	self.ordered[next_id].should_show():
				break

			next_id = next_id + 1

		if next_id == len(self.ordered):
			return self.current

		self.chain.append(original_id)
		self.current_id = next_id

		return self.current
