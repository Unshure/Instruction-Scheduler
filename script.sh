echo "" > output\-a.txt
echo "" > outputOriginal.txt
echo "" > output\-b.txt
echo "" > output\-c.txt
for entry in benchmarks/*
do
  substring=${entry:10:8}
  filetype="-a.iloc"
  folder="benchmarks-a/"
  outputfile="$folder$substring$filetype"
  python3 scheduler.py -a $entry $outputfile
  ./sim < $outputfile >> output\-a.txt
  ./sim < $entry >> outputOriginal.txt
done
for entry in benchmarks/*
do
  substring=${entry:10:8}
  filetype="-b.iloc"
  folder="benchmarks-b/"
  outputfile="$folder$substring$filetype"
  python3 scheduler.py -b $entry $outputfile
  ./sim < $outputfile >> output\-b.txt
done
for entry in benchmarks/*
do
  substring=${entry:10:8}
  filetype="-c.iloc"
  folder="benchmarks-c/"
  outputfile="$folder$substring$filetype"
  python3 scheduler.py -c $entry $outputfile
  ./sim < $outputfile >> output\-c.txt
done


