import requests
rfid1 = "value1"
rfid2 = "value2"
payload = {'nurse': rfid1, 'patient': rfid2} #Change values accordingly
r = requests.post("http://13.127.78.99/auth", data=payload)


print(r.status_code) # If the output is 200 then data is successfully recieved and stored to db
