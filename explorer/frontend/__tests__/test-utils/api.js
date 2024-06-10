import * as utils from '@/utils/server';

export const runAPITest = async (functionToTest, searchCriteria, response, expectedURL, expectedResult, print) => {
	// Arrange:
	const spy = jest.spyOn(utils, 'makeRequest');
	spy.mockResolvedValue(response);

	// Act:
	const result = await functionToTest(searchCriteria);
	const fs = require('fs');
	if (print) fs.writeFileSync('accounts.json', JSON.stringify(result));

	// Assert:
	expect(spy).toHaveBeenCalledWith(expectedURL);
	expect(result).toEqual(expectedResult);
};
