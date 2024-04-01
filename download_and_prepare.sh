cd data
## download interproscan
wget https://ftp.ebi.ac.uk/pub/software/unix/iprscan/5/5.66-98.0/interproscan-5.66-98.0-64-bit.tar.gz
tar -xvf interproscan-5.66-98.0-64-bit.tar.gz
mv interproscan-5.66-98.0 interproscan
rm interproscan-5.66-98.0-64-bit.tar.gz

## download  ECOD
wget http://prodata.swmed.edu/ecod/distributions/ecod.latest.F70.pdb.tar.gz
mkdir ECOD
tar -xvf ecod.latest.F70.pdb.tar.gz -C ECOD
cd -p ECOD
find data -type f -name "*pdb" |xargs -i ln -s {}
cd ..

## download PDB
rsync -rlpt -v -z --delete \
ftp.pdbj.org::ftp_data/structures/divided/mmCIF/ ./mmCIF
mkdir -p pdbDB
cd pdbDB
find ../mmCIF -type f -name "*cif.gz" |xargs -i ln -s {}
cd ..

## for scop
mkdir -p SCOP
cd SCOP
python ../../../structure.py ./mmCIF ../Info/scop-cla-latest.txt.gz
cd ..

## AFDB
mkdir AFDB
mkdir tmp
cd tmp
for i in `cat ../Info/afdb_tar.txt`
do
echo "wget  ftp.ebi.ac.uk/pub/databases/alphafold/v4/${i}"
wget  ftp.ebi.ac.uk/pub/databases/alphafold/v4/${i}
tar -xv ${i}
done
cd ../AFDB
find ../tmp -type f -name "*.pdb.gz"|xargs -i gunzip {}
find ../tmp -type f -name "*.pdb"|xargs -i mv  {} .
cd ..

## make foldseek DB
cd ..
mkdir data/PDB/foldseekDB
mkdir -p data/PDB/foldseekDB/AFDB/
mkdir -p data/PDB/foldseekDB/ECOD/
mkdir -p data/PDB/foldseekDB/pdbDB/
mkdir -p data/PDB/foldseekDB/SCOP2/

docker run -it  \
    --add-host dockerhost:${IP}  \
    --gpus all \
    -v `pwd`:/apps \
    -p 9008:9006 \
    -p 9116:9112 \
    nongbaoting/pisa:latest /bin/bash -c "foldseek createdb  /apps/data/PDB/ /apps/data/PDB/foldseekDB/AFDB/foldseek_PDB_AFDB --threads 12"
docker run -it  \
    --add-host dockerhost:${IP}  \
    --gpus all \
    -v `pwd`:/apps \
    -p 9008:9006 \
    -p 9116:9112 \
    nongbaoting/pisa:latest /bin/bash -c "foldseek createdb  /apps/data/PDB/ /apps/data/PDB/foldseekDB/ECOD/foldseek_ECOD_F70 --threads 12"
docker run -it  \
    --add-host dockerhost:${IP}  \
    --gpus all \
    -v `pwd`:/apps \
    -p 9008:9006 \
    -p 9116:9112 \
    nongbaoting/pisa:latest /bin/bash -c "foldseek createdb  /apps/data/PDB/ /apps/data/PDB/foldseekDB/pdbDB/foldseek_PDB --threads 12"
docker run -it  \
    --add-host dockerhost:${IP}  \
    --gpus all \
    -v `pwd`:/apps \
    -p 9008:9006 \
    -p 9116:9112 \
    nongbaoting/pisa:latest /bin/bash -c "foldseek createdb  /apps/data/PDB/ /apps/data/PDB/foldseekDB/SCOP2/foldseek_scopDomain --threads 12"
