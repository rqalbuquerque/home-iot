from datetime import date, timedelta

class DateRangeSplitter(object):
	"""
	Utility class to split a date range into subranges of up to N days.
	"""
	def __init__(self, max_count_records=30):
		self.max_count_records = max_count_records

	def split(self, start_date: date, end_date: date):
		date_ranges = []
		i_start_date = start_date
		while i_start_date <= end_date:
			i_end_date = i_start_date + timedelta(days=self.max_count_records)
			i_end_date = end_date if i_end_date > end_date else i_end_date
			date_ranges.append((i_start_date,i_end_date))
			i_start_date = i_end_date + timedelta(days=1)
		return date_ranges
