.PHONY: zip

prepare: clean zipfiles

zip: build_en clean zipfiles

zip_cz: build_cz clean zipfiles

clean:
	py3clean .

zipfiles:
	pb_tool zip

build_cz:
	rm constants/__init__.py
	echo 'from .texts_cze import TextConstantsCZ as TextConstants' > constants/__init__.py

build_en:
	rm constants/__init__.py
	echo 'from .texts_en import TextConstantsEN as TextConstants' > constants/__init__.py