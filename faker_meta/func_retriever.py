"""
Faker Function Retriever

Serves as a Faker's own Search Engine. It will retrieve Faker functions based on Fuzzy Search and user input. The search will be done on the method name, as
well as the documentation.

Steps:
    1- Cache all the functions with documentation of each in memory when the API starts.
    2- Receive the user input
    3- Do fuzzy search on the Fake function name.
    4- Check matching percentage and if is < 80% match, then trigger fuzzy on description of the function.
    5- Return to the user a dictionary of the results.

Notes:
     * The response to the user should be in real-time and as soon as the user inputs 2 letters, the fuzzy search should
       start immediately.
     * The user will start getting the results as he types on the app.
"""
