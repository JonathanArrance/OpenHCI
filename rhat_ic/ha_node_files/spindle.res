resource spindle {
    protocol C;
    meta-disk internal;
    disk {
        on-io-error detach;
    }
    device /dev/drbd2;
    startup {
        degr-wfc-timeout 2;
        wfc-timeout 2;
        outdated-wfc-timeout 2;
    }
    #use pacemmaker to do this and start the drbd resource
    syncer {
        verify-alg sha1;
        rate 1000M;
        al-extents 257;
        on-no-data-accessible io-error;
    }
    on %HANODE1% {
        disk   /dev/sdc1;
        address  %HAIP1%:7789;
    }
    #on %HANODE2% {
    #    disk   /dev/sdc1;
    #    address  %HAIP2%:7789;
    #}
    #HANODE#
    on node-dummy { disk   /dev/vg_root2/var; address  169.254.254.253:7789; }
}