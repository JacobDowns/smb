for i in `seq 0 40`;
    do
            python rand_inverse.py $i >> $i.txt &
    done
