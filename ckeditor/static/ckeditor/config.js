/*
Copyright (c) 2003-2011, CKSource - Frederico Knabben. All rights reserved.
For licensing, see LICENSE.html or http://ckeditor.com/license
*/

CKEDITOR.editorConfig = function( config )
{
	// Define changes to default configuration here. For example:
	// config.language = 'fr';
	// config.uiColor = '#AADC6E';
	 config.toolbar = 'MyToolbar';
     	config.toolbar_MyToolbar =
     	[
     	['Image','Flash','Table','HorizontalRule','Smiley','SpecialChar', 'Source'],   
     	['Cut','Copy','Paste','PasteText','PasteFromWord' ],
     	['Undo','Redo','-','Find','Replace','-','SelectAll','RemoveFormat'],
     	'/',
     	['Bold','Italic','Underline','Strike','-','Subscript','Superscript'],
     	['NumberedList','BulletedList','-','Outdent','Indent','Blockquote','CreateDiv'],
     	['JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock'],
     	['Link','Unlink','Anchor']
     	];
};
