echo Check auth
uniq_id=`python3 shop.py put localhost auth flag`
echo "Check auth id: $uniq_id"
python3 shop.py get localhost auth $uniq_id
uniq_id=`python3 shop.py put localhost buy flag2`
echo "Check buy id: $uniq_id"
python3 shop.py get localhost buy $uniq_id