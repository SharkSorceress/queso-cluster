#sudo apt install latexmk texlive-latex-extra
#pip3 install sphinx sphinx-rtd-theme
python3 -m sphinx -d ./_static/source -T -E -b html ./docsrc ./
rm -r ./assets/
mv ./_static/ ./assets/

find ./ -type f -name "*.html" -print0 | xargs -0 sed -i 's/_static/assets/g'
python3 -m sphinx -T -E -b latex ./docsrc ./_pdf
cd ./_pdf/ && pdflatex queso.tex && pdflatex queso.tex && pdflatex queso.tex
mv ./queso.pdf ../ && cd ../ && rm -r _pdf