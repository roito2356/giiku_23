from flask import render_template, Blueprint # 'Blueprint's12-142

error_pages = Blueprint('error_pages', __name__) # s12-142

# s11-130 権限制御２：エラーページの追加 start
@error_pages.app_errorhandler(403) # 'error_pages's12-142
def error_403(error):
    return render_template('error_pages/403.html'), 403

@error_pages.app_errorhandler(404) # 'error_pages's12-142
def error_404(error):
    return render_template('error_pages/404.html'), 404
# s11-130 権限制御２：エラーページの追加 end