DESIRED=$((`date +%s -d "$1"`))
NOW=$((`date +%s`))
if [ $DESIRED -lt $NOW ]; then
	DESIRED=$((`date +%s -d "$1"` + 24*60*60))
fi

sudo killall rtcwake
echo $DESIRED
sudo rtcwake -u -m mem -t $DESIRED &
echo "Suspending..."
sleep 2
clear
echo "Good morning!"
