# Add observatory "HERA" at same position as PAPER_SA. This changes the
# CASA installation -- do this only once per installation.
obstablename=os.getenv("CASAPATH").split()[0]+"/data/geodetic/Observatories/"
tb.open(obstablename, nomodify=False)
paperi=(tb.getcol("Name")=="PAPER_SA").nonzero()[0]
tb.copyrows(obstablename, startrowin=paperi, startrowout=-1, nrow=1)
tb.putcell("Name", tb.nrows()-1, "HERA")
tb.close()
