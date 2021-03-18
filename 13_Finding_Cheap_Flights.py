#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import TimeoutException
import time

import pandas as pd

import smtplib
from email.message import EmailMessage

import schedule

departure_flight_inputs={'Departure': " JFK",
               'Arrival': " LAX",
               'Date': "Jun 20, 2021"}

return_flight_inputs={'Departure': " JFK",
               'Arrival': " ORD",
               'Date': "Aug 28, 2021"}

def find_cheapest_flights(flight_info):
    PATH = 'Path to your chromedriver goes here'
    driver = webdriver.Chrome(executable_path=PATH)

    leaving_from = flight_info['Departure']
    going_to = flight_info['Arrival']
    trip_date = flight_info['Date']
    
    
    #Go to Expedia
    driver.get("https://expedia.com")


    #Click on Flights
    flight_xpath = '//a[@aria-controls="wizard-flight-pwa"]'
    flight_element = WebDriverWait(driver,5).until(
        EC.presence_of_element_located((By.XPATH, flight_xpath))
        )
    flight_element.click()
    time.sleep(0.2)
    
    
    #Click on One-Way. I prefer one way flights
    oneway_xpath = '//a[@aria-controls="wizard-flight-tab-oneway"]' 
    one_way_element = WebDriverWait(driver,5).until(
        EC.presence_of_element_located((By.XPATH, oneway_xpath))
        )
    one_way_element.click()
    time.sleep(0.2)


    #Part 1: Flying From, Flying To, Departure Date, Return Date
    
    #**********************  Complete Leaving From Portion  **********************
    leaving_from_xpath = '//button[@aria-label="Leaving from"]'
    leaving_from_element = WebDriverWait(driver,5).until(
        EC.presence_of_element_located((By.XPATH, leaving_from_xpath))
        )
    leaving_from_element.clear
    leaving_from_element.click()
    time.sleep(1)
    leaving_from_element.send_keys(leaving_from)
    
    time.sleep(1) #Need this otherwise it will be too fast for the broswer
    leaving_from_element.send_keys(Keys.DOWN, Keys.RETURN)
    #**********************  Complete Leaving From Portion  **********************
    
    
    
    #**********************  Complete Going To Portion  **********************
    going_to_xpath = '//button[@aria-label="Going to"]'
    going_to_element = WebDriverWait(driver,5).until(
        EC.presence_of_element_located((By.XPATH, going_to_xpath))
        )
    going_to_element.clear
    going_to_element.click()
    time.sleep(1)
    going_to_element.send_keys(going_to)
    
    time.sleep(1) #Need this otherwise it will be too fast for the broswer
    going_to_element.send_keys(Keys.DOWN, Keys.RETURN) #Go down on item and click on it
    #**********************  Complete Going To Portion  **********************
    
    
    
    #**********************  Complete Departure Date Portion  **********************
    departing_box_xpath = '//button[contains(@aria-label,"Departing")]'
    
    depart_box_element = WebDriverWait(driver,5).until(
        EC.presence_of_element_located((By.XPATH, departing_box_xpath))
        )
    
    depart_box_element.click() #Click on the departure box
    time.sleep(2)
    
    
    #Find the current date. WILL arrow through too
    trip_date_xpath = '//button[contains(@aria-label,"{}")]'.format(trip_date)
    departing_date_element = ""
    while departing_date_element == "":
        try:
            departing_date_element = WebDriverWait(driver,3).until(
            EC.presence_of_element_located((By.XPATH, trip_date_xpath))
            )
            departing_date_element.click() #Click on the departure date
        except TimeoutException:
           departing_date_element=""
           next_month_xpath = '//button[@data-stid="date-picker-paging"][2]'
           driver.find_element_by_xpath(next_month_xpath).click()
           time.sleep(1)
    
    depart_date_done_xpath = '//button[@data-stid="apply-date-picker"]'
    driver.find_element_by_xpath(depart_date_done_xpath).click()
    #**********************  Complete Departure Date Portion  **********************
    
    
    #**********************  Click Search  **********************
    search_button_xpath = '//button[@data-testid="submit-button"]'
    driver.find_element_by_xpath(search_button_xpath).click()
    time.sleep(15) #Need to let the page load properly
    #**********************  Click Search  **********************






    #Part 2: Setting Conditions for our flight
    
    #**********************  Check for Nonstop Flights Sorted by Lowest Price  **********************
    nonstop_flight_xpath = '//input[@id="stops-0"]'
    one_stop_flight_xpath = '//input[@id="stops-1"]'
    
    
    if len(driver.find_elements_by_xpath(nonstop_flight_xpath)) > 0:
        
        driver.find_element_by_xpath(nonstop_flight_xpath).click()
        time.sleep(5)
        
        #Check if there are available flights
        available_flights = driver.find_elements_by_xpath("//span[contains(text(),'Select and show fare information ')]")
        if len(available_flights) >  0:
            if len(available_flights) == 1: #Don't have to sort by prices here
                flights = [(item.text.split(",")[0].split('for')[-1].title(),
                            item.text.split(",")[1].title().replace("At",":"),
                            item.text.split(",")[2].title().replace("At",":"),
                            item.text.split(",")[3].title().replace("At",":")) for item in available_flights[0:5]]

            else:
                #Sort by lowest prices
                driver.find_element_by_xpath('//option[@data-opt-id="PRICE_INCREASING"]').click()
                time.sleep(5)
                flights = [(item.text.split(",")[0].split('for')[-1].title(),
                            item.text.split(",")[1].title().replace("At",":"),
                            item.text.split(",")[2].title().replace("At",":"),
                            item.text.split(",")[3].title().replace("At",":")) for item in available_flights[0:5]]
            
            
            print("Conditions satisfied for: {}:{}, {}:{}, {}:{}".format("Departure",leaving_from,
                                                             "Arrival",going_to,
                                                             "Date",trip_date))
            driver.quit()
            return flights
    else:
        print('Not all conditions could be met for the following: "{}:{}, {}:{}, {}:{}'.format("Departure",leaving_from,
                                                                                             "Arrival",going_to,
                                                                                             "Date",trip_date))
        driver.quit()
        return []
    
    

    #**********************  Check for Nonstop Flights Sorted by Lowest Price  **********************



def send_email():
    #Get return values
    departing_flights = find_cheapest_flights(departure_flight_inputs)
    return_flights = find_cheapest_flights(return_flight_inputs)

    #Put it into a dataframe to visualize this more easily
    df = pd.DataFrame(departing_flights + return_flights)
    
    if not df.empty: #Only send an email if we have actual flight info
        email = open('Your Email Here').read()
        password=open('Your Password Here').read()
        
        msg = EmailMessage()
        
        msg['Subject'] = "Python Flight Info! {} --> {}, Departing: {}, Returning: {}".format(departure_flight_inputs['Departure'], departure_flight_inputs['Arrival'], departure_flight_inputs['Date'],return_flight_inputs['Date'])
        
        msg['From'] = email
        msg['To'] = email
        
        msg.add_alternative('''\
            <!DOCTYPE html>
            <html>
                <body>
                    {}
                </body>
            </html>'''.format(df.to_html()), subtype="html")
    
            
        with smtplib.SMTP_SSL('Email server name here',465) as smtp:
            smtp.login(email,password)
            smtp.send_message(msg)
    

schedule.clear()
schedule.every(30).minutes.do(send_email)

while True:
    schedule.run_pending()
    time.sleep(1)

















