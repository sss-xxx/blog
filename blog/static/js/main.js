/**
 * 简易博客系统的JavaScript功能
 */

// 在DOM加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 自动关闭提示消息
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000); // 5秒后自动关闭
    });

    // 文章内容编辑器增强
    const contentTextarea = document.getElementById('content');
    if (contentTextarea) {
        // 添加Tab键支持
        contentTextarea.addEventListener('keydown', function(e) {
            if (e.key === 'Tab') {
                e.preventDefault();
                const start = this.selectionStart;
                const end = this.selectionEnd;
                
                // 在光标位置插入Tab
                this.value = this.value.substring(0, start) + '    ' + this.value.substring(end);
                
                // 将光标位置移到插入的Tab之后
                this.selectionStart = this.selectionEnd = start + 4;
            }
        });

        // 自动调整高度
        contentTextarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    }

    // 确认删除操作
    const deleteButtons = document.querySelectorAll('a[href*="delete"]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('确定要删除这篇文章吗？')) {
                e.preventDefault();
            }
        });
    });
});