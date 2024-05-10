counter=1
while [ $counter -le 40 ]
do
    echo "Iteration $counter"
    echo "....................."
    mkdir -p /home/avania/projects/python/qboson/JobShopScheduling/data/iteration-$counter
    /home/avania/projects/python/qboson/JobShopScheduling/.venv/bin/python /home/avania/projects/python/qboson/JobShopScheduling/annealers/test.py $counter
    echo "Iteration $counter done"
    counter=$((counter+1))
    echo ""
done 