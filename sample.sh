for i in `seq 0 40`;
    do
            python inverse_noise.py $i >> $i.txt &
    done
