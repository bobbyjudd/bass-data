#!/bin/bash

BASE_URL="https://api.prod2.bassmasterdata.com/v1/data/final-results"

for tourn in `seq 0 10000`;
do
	for pro_or_co in `seq 0 1`;
	do
		FINAL=$(wget -qO- $BASE_URL/$tourn/$pro_or_co)
		LENGTH=${#FINAL}
		if [ $LENGTH -gt 2 ];
		then
			mkdir -p $tourn/$pro_or_co
			# Write final results to file
			echo "$FINAL" >  "$tourn/$pro_or_co/final"

			# Write each day results to file
			for day in `seq 1 4`;
			do
				DAY=$(wget -qO- $BASE_URL/$tourn/$pro_or_co/$day)
				LENGTH=${#DAY}
				if [ $LENGTH -gt 2 ];
				then
					echo "$DAY" >  "$tourn/$pro_or_co/day_$day"
				fi
			done
		echo "Finished $tourn"
		fi
	done
done
