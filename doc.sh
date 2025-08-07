# pushd ugly_bot
# sphinx-build -M html docs/source/ docs/build/
# popd

rm -R ugly_bot/docs/build
sphinx-build -M html ugly_bot/docs/source/ ugly_bot/docs/build/
