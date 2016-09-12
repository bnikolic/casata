PWs=   hera19.mdw
RSTs=  $(PWs:.rstw=.rst)
HTMLs= $(PWs:.rstw=.html)
PDFs=  $(PWs:.mdw=.pdf)

PWEAVE=/data/p/casa-release-4.6.0-el6/bin/pweave
PPATH=../../clplot/:${PYTHONPATH}
RST2HTML=/data/p/casa-release-4.6.0-el6/bin/rst2html5

.PHONY: default
default: ${PDFs}

%.rst: %.rstw 
	PYTHONPATH=${PPATH} ${PWEAVE} $<

%.tex: %.rstw 
	PYTHONPATH=${PPATH} ${PWEAVE} -f pandoc2latex $<

%.tex: %.mdw
	PYTHONPATH=${PPATH} ${PWEAVE} -f pandoc2latex $<

%.pdf: %.tex
	pdflatex $<

%.html: %.rst
	${RST2HTML} $(<:.rstw=.rst)  > $@

.PHONY: clean
clean:
	rm -f ${RSTs} ${HTMLs} ${PDFs} docset.zip
	rm -rf figures

.PHONY: rst
rst: $(RSTs)
.PHONY: html
html: $(HTMLs)

docset.zip: html
	zip -r $@ $^ figures

