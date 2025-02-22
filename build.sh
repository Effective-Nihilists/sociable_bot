pushd sociable_bot

rm -r dist
python -m build   
python -m twine upload dist/*

popd