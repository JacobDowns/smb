for i in `seq 0 40`;
    do
            python inverse_noise1.py $i >> $i.txt &
    done
