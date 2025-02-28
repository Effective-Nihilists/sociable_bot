# pushd sociable_bot
# sphinx-build -M html docs/source/ docs/build/
# popd

rm -R sociable_bot/docs/build
sphinx-build -M html sociable_bot/docs/source/ sociable_bot/docs/build/
