# Securein_assess

1. Make sure you have installed python and mongodb in your local system
2. After cloning this repo, create venv using the command python -m venv venv
3. Then install the project dependencies using pip install -r requirements.txt.
4. Run python main.py
5. You can view the swagger documentation in the following link http://127.0.0.1:8000/docs


# Documentatio for this project

1. I have used pandas to transform the data and used some of the methods to handle null values.
2. I have used mean contribution to fill na values of temprature column as we have less null data.
3. I have used forward fill to fill na values of humidity column as we have less null data.
4. I have used some logic from online to fill the heat index values as there were more null values it is not good to drop those.
5. I have dropped some of the negative pressure values as we don't need that.
6. Whenver you start the server it will do data transforming and save it to mongoDB in case you don't need that comment the line no 27 in main.py.
7. For the first api we need to pass page_offset param if we are querying using month as it will fetch large data i have set the limit to 20 based on that you can provide the offset value
