start=0.0
stop=3.0
step=0.0125

for val in $(seq $start $step $stop)
do
    g4bl ../inputs/window_test.g4bl WinThickness=${val}
done