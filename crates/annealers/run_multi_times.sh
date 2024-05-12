counter=1
while [ $counter -le 4000 ]
do
    echo "Iteration $counter"
    echo "....................."
    /home/avania/projects/python/qboson/JobShopScheduling/.venv/bin/python /home/avania/projects/python/qboson/JobShopScheduling/annealers/run.py $counter
    echo "Iteration $counter done"
    counter=$((counter+1))
    echo ""
done