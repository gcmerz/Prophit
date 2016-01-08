# Prophit
Ajay Nathan, Alexander Suh, Gabriela Merz 

## Welcome to Prophit!

Just as Netflix makes recommendations about movies you would like to watch, 
Prophit makes recommendations to Capital One customers about stores they would 
like to try. Since Capital One has data on their customers' financial situation
and transaction history, they are in a unique position to make recommendations 
about future purchases, especially when that data on individuals is combined 
with the information Capital One has on its merchants, as well as Wolfram 
Alpha's macro data on the state of the economy. Prophit combines all of these 
datapoints in a machine-learning algorithm to predict the kinds of stores that 
customers will like, allowing financial institutions like Capital One to help 
their customers in a new way.  


## Getting Started

Make sure you are using a virtual environment of some sort (e.g. `virtualenv` or
`pyenv`), and make sure you have python 3.

```
pip3 install -r requirements.txt
./manage.py migrate
./manage.py loaddata sites
./manage.py runserver
```

Navigate to the capitalOne folder containing manage.py and do

python3 manage.py runserver

Then open up a browser, go to localhost:8000, and you're at the site! Since we 
made this site under the premise that only Capital One users could use it, there
is no sign-up form on the site: hypothetically, users would sign up by signing
up for an account with Capital One. However, so that you can experience the 
site, we've made an account for you! The username is 'capital', and the password
is 'one'. Enjoy!

## Awards 
This project won "Best Use of Capital One's API" at HackHarvard 2015 
