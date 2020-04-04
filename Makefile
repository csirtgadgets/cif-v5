.PHONY: clean test sdist all dist deploy docker docker-test

all: docker

clean:
	rm -rf `find . | grep \.pyc`
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info

test:
	@python setup.py test 

dist: sdist

sdist:
	@python setup.py sdist

deploy: clean dist
	twine upload -r csirtg dist/cif-5*.tar.gz

docker-test:
	-(cd docker && docker-compose up -d && bash test.sh && docker-compose down)

docker: clean sdist
	-(cd docker && bash build.sh)

docker-down:
	-(cd docker && docker-compose down)

docker-tag:
	-(cd docker && bash tag.sh)

docker-upload: docker-tag
	-(cd docker && bash upload.sh)
