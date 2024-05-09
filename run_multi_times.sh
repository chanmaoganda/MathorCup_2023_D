counter=1
while [ $counter -le 40 ]
do
    echo "Iteration $counter"
    echo "....................."
    /home/avania/projects/python/qboson/JobShopScheduling/.venv/bin/python /home/avania/projects/python/qboson/JobShopScheduling/test.py
    echo "Iteration $counter done"
    counter=$((counter+1))
    echo ""
done