The sass variable overrides to be used in the enthought theme 
are added here so that the THEME is solely used for CSS 
overrides.

The CSS source ordering is changed by changing code in the 
following mako templates that render some scss files: 
- `lms-main.scss.mako`, and 
- `lms-course.scss.mako`

So now, the source order for SASS files is like:
1. some common dependencies like mixin libs, etc
2. Enthought's SASS variable overrides
3. Main `build-*` index file for main stylesheet or 
   course stylesheet (examples)
4. Custom theme's SASS

