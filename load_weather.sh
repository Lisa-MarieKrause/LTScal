#!/bin/sh


.PHONY: all clean

SHELL := bash

all: scrape convert load

scrape:
	curl --request GET --url https://api.tomorrow.io/v4/timelines -G \
	-d location=51.350129,12.343234 \
	-d fields=temperature,temperatureApparent,precipitationProbability,precipitationIntensity,windSpeed,cloudCover,weatherCode \
	-d timesteps=1h \
	-d units=metric \
	-d apikey=$(TOMORROW_API_KEY) > weather_fc_hours.json

	touch $@

convert: scrape
	jq .data.timelines[0].intervals weather_fc_hours.json | jq -r 'map("\(.startTime), \(.values.temperature), \(.values.precipitationProbability), \(.values.precipitationIntensity), \(.values.windSpeed), \(.values.cloudCover), \(.values.weatherCode)") as $$rows | $$rows[] ' > weather_fc_hours.csv

	touch $@

load: convert
	/usr/bin/sqlite3 ./instance/LTS.sqlite -cmd ".mode csv" ".import weather_fc_hours.csv weatherTemp"
	/usr/bin/sqlite3 ./instance/LTS.sqlite -cmd "INSERT INTO weatherForecast (startTime,temperature, precipitationProbability,precipitationIntensity,windSpeed, cloudCover, weatherCode) SELECT * FROM weatherTemp;" "DROP TABLE weatherTemp;"

clean: scrape convert
	rm scrape
	rm convert
	rm weather_fc_hours.json
	rm weather_fc_hours.csv

