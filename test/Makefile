PWs=   clplot.rstw
RSTs=  $(PWs:.rstw=.rst)
HTMLs= $(PWs:.rstw=.html)

ifeq ($(OS),Windows_NT)
	PWEAVE=pweave.bat
	PPATH=..\;${PYTHONPATH}
	RST2HTML="python.exe" "C:\Users\Bojan\Anaconda\Scripts\rst2html.py"
else
	PWEAVE=/data/p/casa-release-4.6.0-el6/bin/pweave
	PPATH=../clplot:${PYTHONPATH}
	RST2HTML=/data/p/casa-release-4.6.0-el6/bin/rst2html5
endif

.PHONY: default
default: docset.zip

%.rst: %.rstw 
	PYTHONPATH=${PPATH} ${PWEAVE} $<

%.html: %.rst
	${RST2HTML} $(<:.rstw=.rst)  > $@

.PHONY: clean
clean:
	rm -f ${RSTs} ${HTMLs} docset.zip
	rm -rf figures

.PHONY: rst
rst: $(RSTs)
.PHONY: html
html: $(HTMLs)

docset.zip: html
	zip -r $@ $^ figures

clean:
	rm $(RSTs) $(HTMLs)
