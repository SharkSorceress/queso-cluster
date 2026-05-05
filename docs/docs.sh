python3 -m sphinx -d ./docs/man/_static/source -T -E -b html ./docs/docsrc ./docs/man
rm -r ./docs/man/assets/
mv ./docs/man/_static/ ./docs/man/assets/

find ./docs/man/ -type f -name "*.html" -print0 | xargs -0 sed -i 's/_static/assets/g'
python3 -m sphinx -T -E -b latex ./docs/docsrc ./_pdf
cd ./_pdf/ && pdflatex queso.tex && pdflatex queso.tex && pdflatex queso.tex
mv ./queso.pdf ../ && cd ../ && rm -r _pdf