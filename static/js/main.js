$(document).ready(function () {
    function initTelegram() {
        const tg = Telegram.WebApp;
        tg.BackButton.show();

        tg.BackButton.onClick(function () {
            if (location.pathname === '/') {
                tg.close();
            } else {
                window.history.back();
            }
        });


    }

    initTelegram();

    const $input = $('.search-input');
    const $overlay = $('#searchOverlay');

    function setOverlayHeight() {
        $overlay.get(0).style.height = document.querySelector('body').scrollHeight + 'px';
    }

    const toggle = document.getElementById('themeToggle');

    if (localStorage.getItem('theme') === 'dark') {
        document.body.classList.add('dark');
        toggle.checked = true;
    }

    toggle.addEventListener('change', function () {
        document.body.classList.toggle('dark');
        if (document.body.classList.contains('dark')) {
            localStorage.setItem('theme', 'dark');
        } else {
            localStorage.setItem('theme', 'light');
        }
    });

    if ($input.length && $overlay.length) {
        $input.on('focus', function (e) {
            e.stopPropagation();
            $overlay.removeClass('d-none');
            setOverlayHeight();
        });

        /*
        $overlay.on('click', function () {
            $overlay.addClass('d-none');
            $input.blur();
        });
        */

        $(document).on('click', 'body', function (e) {
            if ($overlay.hasClass('d-none')) return;
            console.log(e.target);
            if (e.target.classList.contains('search-input')) return;


            $overlay.addClass('d-none');
            $input.blur();

        });
    }

    $(document).on('click', '.badge-item', function () {
        const category_id = $(this).attr('attr-id');
        $.get('/search-product/?tg=1', { category_ids: category_id }, function (data) {
            $('#products_list').html(data['html']);
        });
    });

    $(document).on('input', '.search-input', function () {
        const query = $(this).val().trim();

        if (query.length > 3) {
            $.get('/search-product/?tg=1', { product_name: query }, function (data) {
                $('#products_list').html(data['html']);
            });
        }
    });

    var backdrop = $('[data-backdrop]');
    var catalogFilter = $('[data-catalog-filter]');

    function showBackDrop() {
        backdrop.fadeIn();
    }
    function hideBackDrop() {
        backdrop.fadeOut();
    }

    backdrop.on('click', function () {
        hideBackDrop();
        catalogFilter.fadeOut().removeClass('active');
    });

    $(document).on('click', '[data-show-filter-btn]', function () {
        showBackDrop();
        catalogFilter.fadeIn(50).addClass('active');
    });

    $(document).on('click', '[data-filter-close]', function () {
        hideBackDrop();
        catalogFilter.fadeOut().removeClass('active');
    });

    $(document).on('click', '.filter-start', function () {
        const selectedCategoriesIds = $('.filter-chip:checked').map(function () {
            return $(this).attr('attr-id');
        }).get();

        const category_ids = selectedCategoriesIds.join(',');
        const sortFilter = $('#filter-sort').val();

        $.get('/search-product/?tg=1', { category_ids: category_ids, order_by: sortFilter }, function (data) {
            $('#products_list').html(data['html']);
            hideBackDrop();
            catalogFilter.removeClass('active');
        });
    });



    // lazy load catalog

    var lazyLoadTrigger = $('[data-lazyload-anchor]');
    function elementIsVisibleInViewport(el, partiallyVisible = false) {
        var { top, left, bottom, right } = el.getBoundingClientRect();
        var { innerHeight, innerWidth } = window;
        return partiallyVisible
            ? ((top > 0 && top < innerHeight) ||
                (bottom > 0 && bottom < innerHeight)) &&
            ((left > 0 && left < innerWidth) || (right > 0 && right < innerWidth))
            : top >= 0 && left >= 0 && bottom <= innerHeight && right <= innerWidth;
    };

    var fetchingProductsActive = false;
    var limit = 20;
    var offset = $(document).find('[data-product-element]').length;
    var endOfList = false;
    $(document).on('scroll', function () {
        if (elementIsVisibleInViewport(lazyLoadTrigger.get(0)) && !fetchingProductsActive && !endOfList) {
            fetchingProductsActive = true;
            $.ajax({
                url: window.location.href.split('?')[0],
                data: {
                    limit: limit,
                    offset: offset
                },
                type: 'get',
                dataType: 'html',
                success: function (data) {
                    fetchingProductsActive = false;
                    var elements = $(data).find('[data-product-element]');
                    offset = offset + elements.length;
                    if (elements.length === 0)
                        endOfList = true;
                    else {
                        $('#products_list').append(elements);
                    }
                },
            });
        }
    });

    $('#productCarousel').on('slide.bs.carousel', function () {
        $(this).find('video').each(function () {
            this.pause();
            this.currentTime = 0;
        });
    });

    $('#productCarousel').on('slid.bs.carousel', function () {
        $(this).find('.carousel-item.active video').each(function () {
            this.play();
        });
    });

    $('#productCarousel .carousel-item.active video').each(function () { this.play(); });

});