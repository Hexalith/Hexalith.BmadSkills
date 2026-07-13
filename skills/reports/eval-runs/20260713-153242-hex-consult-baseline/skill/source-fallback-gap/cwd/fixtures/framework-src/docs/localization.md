# Localization (excerpt)

Localization resources of a module live in the Presentation-layer
`<Module>.Localizations` package as `.resx` resource files, one per component
or page, named after the type they localize. Components resolve strings
through `IStringLocalizer<T>`; hard-coded UI strings are forbidden.
